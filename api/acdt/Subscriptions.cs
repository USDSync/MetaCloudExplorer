using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace acdt
{

    public class Subscriptions : List<Subscription> { }

    public class Subscription
    {
        public string Id { get; set; }
        public string Name { get; set; }
        public string Description { get; set; }
        public string ParentAAD { get; set; }

        public int ResourceCount { get; set; }
        public float x { get; set; }
        public float y { get; set; }
        public float z { get; set; }

    }
}
