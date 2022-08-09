using Microsoft.VisualBasic.FileIO;
using System;
using System.Collections.Generic;
using acdt;

namespace acdt
{
    internal class Program
    {
        private static string rootPath= @"F:\Source\Github\AzureCloudDigitalTwin\exts\endiverse.azure.twin\";
        private static string companyName = "Company1";
            
        static void Main(string[] args)
        {
            
            string rgfilename = args[0];
            string allfilename = args[1];

            ResourceGroups grps = LoadGroupsFromFile(rgfilename);
            Resources res = LoadResourcesFromFile(allfilename);
            //CalcCounts(grps, res);

            CreateAADDataMap(res);
            CreateResourceGroupDataMap(res, grps);
            CreateResourceMap(res);
            CreateTypeCountMap(res);
        }

        private static void CreateTypeCountMap(Resources res)
        {
            //Console.WriteLine("\r\n--- Resource Count By Group ---");
            Dictionary<string, int> rgs = ResourceAggregator.CountByType(res);

            foreach(KeyValuePair<string, int> kvp in rgs)
            {
                Console.WriteLine(kvp.Key, kvp.Value);
            }
            

        }

        private static void CreateResourceGroupDataMap(Resources res, ResourceGroups grps)
        {
            //Console.WriteLine("\r\n--- Resource Count By Group ---");
            Dictionary<string, int> rgs = ResourceAggregator.CountByGroup(res);

            //The Width and Height to use for each item buffer
            int rt = 20;
            float tw = 2.5F, th = 4.0F;
            float x = 3, y = 0, z = 0;

            ResourceGroups grpList = new ResourceGroups();

            foreach (KeyValuePair<string, int> rg in rgs)
            {
                foreach (ResourceGroup grp in grps)
                {
                    if (grp.Name == rg.Key)
                    {

                        // Console.WriteLine(String.Format("{0} - {1}", sub.Key, sub.Value));
                        grpList.Add(new ResourceGroup()
                        {
                            Name = rg.Key,
                            Location = grp.Location,
                            Subscription = grp.Subscription,
                            ResourceCount = rg.Value,
                            x = x,
                            y = y,
                            z = z
                        });

                        //New Row
                        if (x + tw > rt)
                        {
                            //reset
                            y += th;
                            x = 0;
                        }
                        else
                        {
                            //Move column pos
                            x += tw;
                        }

                    }

                }

            }

            grpList.ExportToTextFile<ResourceGroup>(rootPath + @"data\export\" + companyName + "_Groups.csv", ',');
        }


        private static void CreateResourceMap(Resources res)
        {
            //The Width and Height to use for each item buffer
            int rt = 20;
            int rd = 40;
            float tw = 2.5F, th = 4.0F;
            float x = 3, y = 0, z = 0;

            foreach (Resource resource in res)
            {
                resource.x = x;
                resource.y = y;
                resource.z = z;

                //New Row
                if (x + tw > rt)
                {
                    //reset
                    y += th;
                    x = 0;
                }
                else
                {
                    //Move column pos
                    x += tw;
                }
            }

            res.ExportToTextFile<Resource>(rootPath + @"data\export\" + companyName + "_Res.csv", ',');
        }

        
        private static void CreateAADDataMap(Resources res)
        {
            //Console.WriteLine("\r\n--- Resource Count By Subscription ---");
            Dictionary<string, int> subs = ResourceAggregator.CountBySubscription(res);

            //The Width and Height to use for each item buffer
            int rt = 20;
            float tw = 3F, th = 4.0F;
            float x = 3, y = 0, z = 0;

            Subscriptions subsList = new Subscriptions();

            foreach (KeyValuePair<string, int> sub in subs)
            {
                // Console.WriteLine(String.Format("{0} - {1}", sub.Key, sub.Value));
                subsList.Add(new Subscription()
                {
                    Name = sub.Key,
                    ResourceCount = sub.Value,
                    x = x,
                    y = y,
                    z = z 
                });

                //New Row
                if (x + tw > rt)
                {
                    //reset
                    y += th;
                    x = 0;
                }
                else
                {
                    //Move column pos
                    x += tw;
                }

            }

            subsList.ExportToTextFile<Subscription>(rootPath + @"data\export\" + companyName + "_Subs.csv", ',');
        }

        private static void CalcCounts(ResourceGroups grps, Resources res)
        {
            //Calculate Counts
            //By Subscription
            Console.WriteLine("\r\n--- Resource Count By Subscription ---");
            Dictionary<string, int> subs = ResourceAggregator.CountBySubscription(res);

            foreach (KeyValuePair<string, int> sub in subs)
            {
                Console.WriteLine(String.Format("{0} - {1}", sub.Key, sub.Value));
            }
            
            //By Group Location
            Dictionary<string, int> locations = ResourceAggregator.GroupCountByLocation(grps);

            Console.WriteLine("\r\n--- Group Count By Location ---");
            foreach (KeyValuePair<string, int> location in locations)
            {
                Console.WriteLine(String.Format("{0} - {1}", location.Key, location.Value));
            }

            //By Resource Location
            Dictionary<string, int> resLocations = ResourceAggregator.ResourceCountByLocation(res);

            Console.WriteLine("\r\n--- Resource Count By Location ---");
            foreach (KeyValuePair<string, int> location in resLocations)
            {
                Console.WriteLine(String.Format("{0} - {1}", location.Key, location.Value));
            }


            //By Type
            Console.WriteLine("\r\n--- Resource Count By Type ---");
            Dictionary<string, int> types = ResourceAggregator.CountByType(res);

            foreach (KeyValuePair<string, int> type in types)
            {
                Console.WriteLine(String.Format("{0} - {1}", type.Key, type.Value));
            }

            //By Group
            Console.WriteLine("\r\n--- Resource Count By Group ---");
            Dictionary<string, int> groups = ResourceAggregator.CountByGroup(res);

            foreach (KeyValuePair<string, int> group in groups)
            {
                Console.WriteLine(String.Format("{0} - {1}", group.Key, group.Value));
            }



            //By Cost - tbd
        }

        private static Resources LoadResourcesFromFile(string filename)
        {
            Resources res = new Resources();

            using (TextFieldParser parser = new TextFieldParser(filename))
            {
                parser.TextFieldType = FieldType.Delimited;
                parser.SetDelimiters(",");
                while (!parser.EndOfData)
                {
                    //Processing row
                    string[] fields = parser.ReadFields();

                    if (fields[0] == "NAME") continue;

                    res.Add(new Resource()
                    {
                        Name = fields[0],
                        Location = fields[3],
                        Subscription = fields[4],
                        Group = fields[2],
                        Type = fields[1],
                    });
                }
            }
            return res;
        }

        private static ResourceGroups LoadGroupsFromFile(string filename)
        {
            ResourceGroups res = new ResourceGroups();

            using (TextFieldParser parser = new TextFieldParser(filename))
            {
                parser.TextFieldType = FieldType.Delimited;
                parser.SetDelimiters(",");
                while (!parser.EndOfData)
                {
                    //Processing row
                    string[] fields = parser.ReadFields();
                    
                    if (fields[0] == "NAME") continue;

                    res.Add(new ResourceGroup()
                    {
                        Name = fields[0],
                        Location = fields[2],
                        Subscription = fields[1],
                    });
                    
                }
            }
            return res;
        }
    }
}
